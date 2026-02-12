import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { strategyAPI, backtestAPI, strategyTypesAPI } from '../services/api'
import type { StrategyCreate, StrategyUpdate } from '../types/api'
import BacktestModal from '../components/Backtest/BacktestModal'

const { Option } = Select

const StrategyList: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingStrategy, setEditingStrategy] = useState<any>(null)
  const [backtestModalVisible, setBacktestModalVisible] = useState(false)
  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('')
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [selectedStrategyType, setSelectedStrategyType] = useState<string>('')

  const { data: strategies, isLoading } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyAPI.list(),
  })

  // 获取可用的策略类型
  const { data: strategyTypes, isLoading: isLoadingTypes, error: typesError } = useQuery({
    queryKey: ['strategy-types'],
    queryFn: () => strategyTypesAPI.list(),
  })

  // 调试：检查策略类型数据
  useEffect(() => {
    if (typesError) {
      console.error('获取策略类型失败:', typesError)
    }
    if (strategyTypes) {
      console.log('策略类型数据:', strategyTypes)
      console.log('可用策略数量:', strategyTypes.available?.length)
    }
  }, [strategyTypes, typesError])

  // 调试：检查策略类型数据
  if (typesError) {
    console.error('获取策略类型失败:', typesError)
  }
  if (strategyTypes) {
    console.log('策略类型数据:', strategyTypes)
  }

  const createMutation = useMutation({
    mutationFn: (data: StrategyCreate) => strategyAPI.create(data),
    onSuccess: () => {
      message.success('策略创建成功')
      setIsModalVisible(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
    onError: (error: Error) => {
      console.error('创建策略失败:', error)
      const errorMsg = error.message || '未知错误'
      message.error(`创建失败: ${errorMsg}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: StrategyUpdate }) =>
      strategyAPI.update(id, data),
    onSuccess: () => {
      message.success('策略更新成功')
      setIsModalVisible(false)
      setEditingStrategy(null)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
    onError: (error: Error) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => strategyAPI.delete(id),
    onSuccess: () => {
      message.success('策略删除成功')
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
    onError: (error: Error) => {
      message.error(`删除失败: ${error.message}`)
    },
  })

  const handleCreate = () => {
    setEditingStrategy(null)
    setSelectedStrategyType('')
    setIsModalVisible(true)
    form.resetFields()
  }

  const handleEdit = (record: any) => {
    setEditingStrategy(record)
    setSelectedStrategyType(record.strategy_type)
    setIsModalVisible(true)
    form.setFieldsValue(record)
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  const handleRunBacktest = (strategyId: string) => {
    setSelectedStrategyId(strategyId)
    setBacktestModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingStrategy) {
        updateMutation.mutate({ id: editingStrategy.id, data: values })
      } else {
        createMutation.mutate(values as StrategyCreate)
      }
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  // 获取策略类型的中文标签和描述
  const getStrategyTypeInfo = (strategyType: string) => {
    const type = strategyTypes?.available.find(t => t.value === strategyType)
    return {
      label: type?.label || strategyType,
      description: type?.description || '暂无描述'
    }
  }

  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '策略类型',
      dataIndex: 'strategy_type',
      key: 'strategy_type',
      render: (text: string) => {
        const info = getStrategyTypeInfo(text)
        return (
          <div>
            <div style={{ fontWeight: 'bold' }}>{info.label}</div>
            <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
              {info.description.length > 60 
                ? `${info.description.substring(0, 60)}...` 
                : info.description}
            </div>
          </div>
        )
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: string) => new Date(text).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            onClick={() => handleRunBacktest(record.id)}
          >
            回测
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个策略吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>策略管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          创建策略
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={strategies}
        loading={isLoading}
        rowKey="id"
      />

      <Modal
        title={editingStrategy ? '编辑策略' : '创建策略'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setIsModalVisible(false)
          setEditingStrategy(null)
          setSelectedStrategyType('')
          form.resetFields()
        }}
        confirmLoading={createMutation.isPending || updateMutation.isPending}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="策略名称"
            rules={[{ required: true, message: '请输入策略名称' }]}
          >
            <Input placeholder="请输入策略名称" />
          </Form.Item>
          <Form.Item
            name="strategy_type"
            label="策略类型"
            rules={[{ required: true, message: '请选择策略类型' }]}
          >
            <Select 
              placeholder="请选择策略类型"
              onChange={(value) => setSelectedStrategyType(value)}
              loading={isLoadingTypes}
              notFoundContent={isLoadingTypes ? '加载中...' : (typesError ? '加载失败' : '暂无数据')}
            >
              {strategyTypes?.available && strategyTypes.available.length > 0 ? (
                strategyTypes.available.map((type) => (
                  <Option 
                    key={type.value} 
                    value={type.value}
                    disabled={!type.registered}
                  >
                    {type.label}
                    {!type.registered && (
                      <Tag color="orange" style={{ marginLeft: 8 }}>
                        未实现
                      </Tag>
                    )}
                  </Option>
                ))
              ) : null}
            </Select>
          </Form.Item>
          {/* 显示选中策略类型的描述 */}
          {selectedStrategyType && strategyTypes && (
            <div style={{ 
              marginTop: -16, 
              marginBottom: 16,
              padding: '12px',
              backgroundColor: '#f5f5f5',
              borderRadius: '4px',
              border: '1px solid #d9d9d9',
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#1890ff' }}>
                策略类型描述：
              </div>
              <div 
                style={{ 
                  color: '#666', 
                  lineHeight: '1.8', 
                  fontSize: '14px',
                  whiteSpace: 'pre-line'
                }}
              >
                {strategyTypes.available.find(t => t.value === selectedStrategyType)?.description || '暂无描述'}
              </div>
            </div>
          )}
          {strategyTypes && (
            <div style={{ fontSize: '12px', color: '#999', marginTop: -16, marginBottom: 16 }}>
              {strategyTypes.available.filter(t => !t.registered).length > 0 && (
                <span>
                  提示：标记为"未实现"的策略类型暂不可用
                </span>
              )}
            </div>
          )}
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={4} placeholder="请输入策略描述" />
          </Form.Item>
        </Form>
      </Modal>

      <BacktestModal
        visible={backtestModalVisible}
        strategyId={selectedStrategyId}
        onClose={() => {
          setBacktestModalVisible(false)
          setSelectedStrategyId('')
        }}
      />
    </div>
  )
}

export default StrategyList

