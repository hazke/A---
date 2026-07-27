import { useMemo, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Input,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import {
  CameraOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import dayjs from 'dayjs'
import { perceptionAPI } from '../services/api'
import type {
  FieldStatus,
  FrozenSnapshot,
  LivePerception,
  NullableMetric,
} from '../types/api'

const { Title, Text, Paragraph } = Typography

const STATUS_COLOR: Record<FieldStatus, string> = {
  ok: 'success',
  missing: 'error',
  stale: 'warning',
  degraded: 'default',
}

const STATUS_LABEL: Record<FieldStatus, string> = {
  ok: '正常',
  missing: '缺失',
  stale: '过期',
  degraded: '降级',
}

function formatMetric(metric?: NullableMetric, digits = 2): string {
  if (!metric || metric.status !== 'ok' || metric.value == null) {
    return '—'
  }
  const suffix = metric.unit === '%' ? '%' : metric.unit ? ` ${metric.unit}` : ''
  return `${metric.value.toFixed(digits)}${suffix}`
}

function MetricTag({ metric }: { metric?: NullableMetric }) {
  if (!metric) return <Tag color="error">缺失</Tag>
  return <Tag color={STATUS_COLOR[metric.status]}>{STATUS_LABEL[metric.status]}</Tag>
}

function QualityBanner({ data }: { data: LivePerception }) {
  const { quality } = data
  const type = quality.passed ? 'success' : quality.overall_status === 'degraded' ? 'warning' : 'error'
  const icon = quality.passed ? (
    <CheckCircleOutlined />
  ) : quality.overall_status === 'degraded' ? (
    <WarningOutlined />
  ) : (
    <CloseCircleOutlined />
  )

  return (
    <Alert
      type={type}
      showIcon
      icon={icon}
      message={
        <Space wrap>
          <Text strong>数据质量</Text>
          <Tag color={STATUS_COLOR[quality.overall_status]}>
            {STATUS_LABEL[quality.overall_status]}
          </Tag>
          <Text type="secondary">
            SLA {quality.freshness_sla_seconds}s · {quality.flags.length} 条标记
          </Text>
          {quality.passed ? (
            <Text type="success">可进入下游智能体</Text>
          ) : (
            <Text type="danger">存在关键缺失/过期字段，下游应 HOLD</Text>
          )}
        </Space>
      }
      description={
        quality.flags.length > 0 ? (
          <Table
            size="small"
            pagination={false}
            style={{ marginTop: 8 }}
            rowKey={(row) => `${row.field_path}-${row.message}`}
            dataSource={quality.flags}
            columns={[
              { title: '字段', dataIndex: 'field_path', width: 220 },
              {
                title: '状态',
                dataIndex: 'status',
                width: 80,
                render: (status: FieldStatus) => (
                  <Tag color={STATUS_COLOR[status]}>{STATUS_LABEL[status]}</Tag>
                ),
              },
              { title: '说明', dataIndex: 'message' },
              { title: '来源', dataIndex: 'source', width: 200 },
            ]}
          />
        ) : (
          '所有关键字段通过质量检查'
        )
      }
    />
  )
}

function SnapshotInspector({ snapshot }: { snapshot: FrozenSnapshot | null }) {
  if (!snapshot) {
    return (
      <Card title="冻结快照">
        <Text type="secondary">尚未冻结快照。点击「冻结快照」保存当前感知状态。</Text>
      </Card>
    )
  }

  return (
    <Card
      title="冻结快照"
      extra={
        <Space>
          <Tag color="blue">{snapshot.snapshot_id.slice(0, 8)}…</Tag>
          <Text type="secondary">{dayjs(snapshot.frozen_at).format('YYYY-MM-DD HH:mm:ss')}</Text>
        </Space>
      }
    >
      <Descriptions bordered size="small" column={2}>
        <Descriptions.Item label="快照 ID">{snapshot.snapshot_id}</Descriptions.Item>
        <Descriptions.Item label="标的">{snapshot.symbol}</Descriptions.Item>
        <Descriptions.Item label="冻结时间">
          {dayjs(snapshot.frozen_at).format('YYYY-MM-DD HH:mm:ss')}
        </Descriptions.Item>
        <Descriptions.Item label="质量">
          <Tag color={STATUS_COLOR[snapshot.quality.overall_status]}>
            {STATUS_LABEL[snapshot.quality.overall_status]}
          </Tag>
        </Descriptions.Item>
      </Descriptions>
      <Paragraph style={{ marginTop: 16 }}>
        <Text strong>原始 JSON</Text>
      </Paragraph>
      <pre
        style={{
          background: '#f5f5f5',
          padding: 12,
          borderRadius: 6,
          maxHeight: 360,
          overflow: 'auto',
          fontSize: 12,
        }}
      >
        {JSON.stringify(snapshot, null, 2)}
      </pre>
    </Card>
  )
}

const DataPerception: React.FC = () => {
  const [symbol, setSymbol] = useState('601138')
  const queryClient = useQueryClient()

  const {
    data: live,
    isLoading,
    isFetching,
    refetch,
    error,
  } = useQuery({
    queryKey: ['perception-live', symbol],
    queryFn: () => perceptionAPI.getLive(symbol),
    refetchInterval: 30_000,
  })

  const { data: latestSnapshot } = useQuery({
    queryKey: ['perception-snapshot-latest', symbol],
    queryFn: () => perceptionAPI.getLatestSnapshot(symbol),
    retry: false,
  })

  const freezeMutation = useMutation({
    mutationFn: () => perceptionAPI.freezeSnapshot(symbol),
    onSuccess: (response) => {
      message.success(`快照已冻结: ${response.snapshot.snapshot_id.slice(0, 8)}…`)
      queryClient.setQueryData(['perception-snapshot-latest', symbol], response.snapshot)
    },
    onError: (err: Error) => message.error(err.message),
  })

  const capitalFlowRows = useMemo(() => {
    if (!live) return []
    const buckets = [
      ['主力', live.capital_flow.main],
      ['超大单', live.capital_flow.super_large],
      ['大单', live.capital_flow.large],
      ['中单', live.capital_flow.medium],
      ['小单', live.capital_flow.small],
    ]
    return buckets.map(([label, bucket]) => ({
      key: label,
      label,
      net_inflow: bucket.net_inflow,
    }))
  }, [live])

  return (
    <div>
      <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between' }} wrap>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            数据感知 · Stage 01
          </Title>
          <Text type="secondary">AgenticQ 控制塔 — 实时感知与冻结快照</Text>
        </div>
        <Space wrap>
          <Input
            addonBefore="标的"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.trim())}
            style={{ width: 160 }}
            maxLength={6}
          />
          <Button icon={<ReloadOutlined />} onClick={() => refetch()} loading={isFetching}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<CameraOutlined />}
            loading={freezeMutation.isPending}
            onClick={() => freezeMutation.mutate()}
            disabled={!live}
          >
            冻结快照
          </Button>
        </Space>
      </Space>

      {error && (
        <Alert
          type="error"
          showIcon
          message="加载失败"
          description={(error as Error).message}
          style={{ marginBottom: 16 }}
        />
      )}

      {live && (
        <>
          <div style={{ marginBottom: 16 }}>
            <QualityBanner data={live} />
          </div>

          <Row gutter={[16, 16]}>
            <Col xs={24} lg={14}>
              <Card
                title={`行情 · ${live.market.name || live.symbol}`}
                loading={isLoading}
                extra={
                  <Text type="secondary">
                    {dayjs(live.collected_at).format('HH:mm:ss')}
                  </Text>
                }
              >
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="最新价"
                      value={formatMetric(live.market.last_price)}
                      suffix={<MetricTag metric={live.market.last_price} />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="涨跌幅"
                      value={formatMetric(live.market.change_pct)}
                      suffix={<MetricTag metric={live.market.change_pct} />}
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="成交额"
                      value={formatMetric(live.market.amount, 0)}
                      suffix={<MetricTag metric={live.market.amount} />}
                    />
                  </Col>
                </Row>
                <Descriptions bordered size="small" column={3} style={{ marginTop: 16 }}>
                  <Descriptions.Item label="今开">{formatMetric(live.market.open)}</Descriptions.Item>
                  <Descriptions.Item label="最高">{formatMetric(live.market.high)}</Descriptions.Item>
                  <Descriptions.Item label="最低">{formatMetric(live.market.low)}</Descriptions.Item>
                  <Descriptions.Item label="昨收">{formatMetric(live.market.prev_close)}</Descriptions.Item>
                  <Descriptions.Item label="成交量">{formatMetric(live.market.volume, 0)}</Descriptions.Item>
                  <Descriptions.Item label="换手率">{formatMetric(live.market.turnover_rate)}</Descriptions.Item>
                  <Descriptions.Item label="VWAP">
                    {formatMetric(live.market.vwap)} <MetricTag metric={live.market.vwap} />
                  </Descriptions.Item>
                  <Descriptions.Item label="买卖价差" span={2}>
                    {formatMetric(live.market.bid_ask_spread)}{' '}
                    <MetricTag metric={live.market.bid_ask_spread} />
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            <Col xs={24} lg={10}>
              <Card title="资金流向" loading={isLoading}>
                <Table
                  size="small"
                  pagination={false}
                  dataSource={capitalFlowRows}
                  columns={[
                    { title: '类型', dataIndex: 'label', width: 80 },
                    {
                      title: '净流入',
                      dataIndex: 'net_inflow',
                      render: (metric: NullableMetric) => formatMetric(metric, 0),
                    },
                    {
                      title: '状态',
                      dataIndex: 'net_inflow',
                      width: 80,
                      render: (metric: NullableMetric) => <MetricTag metric={metric} />,
                    },
                  ]}
                />
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="板块 / ETF" loading={isLoading}>
                <Table
                  size="small"
                  pagination={false}
                  rowKey="code"
                  dataSource={[
                    ...live.sector_theme.sectors.map((s) => ({ ...s, kind: '板块' })),
                    ...live.sector_theme.etfs.map((s) => ({ ...s, kind: 'ETF' })),
                  ]}
                  columns={[
                    { title: '类型', dataIndex: 'kind', width: 60 },
                    { title: '名称', dataIndex: 'name' },
                    { title: '代码', dataIndex: 'code', width: 90 },
                    {
                      title: '涨跌幅',
                      dataIndex: 'change_pct',
                      render: (m: NullableMetric) => formatMetric(m),
                    },
                    {
                      title: '状态',
                      dataIndex: 'change_pct',
                      width: 80,
                      render: (m: NullableMetric) => <MetricTag metric={m} />,
                    },
                  ]}
                />
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="全球 AI 上下文" loading={isLoading}>
                <Table
                  size="small"
                  pagination={false}
                  rowKey="symbol"
                  dataSource={live.global_context.tickers}
                  columns={[
                    { title: '标的', dataIndex: 'symbol', width: 80 },
                    { title: '名称', dataIndex: 'name' },
                    {
                      title: '最新价',
                      dataIndex: 'last_price',
                      render: (m: NullableMetric) => formatMetric(m),
                    },
                    {
                      title: '涨跌幅',
                      dataIndex: 'change_pct',
                      render: (m: NullableMetric) => formatMetric(m),
                    },
                  ]}
                />
              </Card>
            </Col>

            <Col span={24}>
              <SnapshotInspector snapshot={latestSnapshot ?? null} />
            </Col>
          </Row>
        </>
      )}
    </div>
  )
}

export default DataPerception
