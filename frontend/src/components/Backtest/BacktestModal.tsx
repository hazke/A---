import { useState } from 'react'
import { Modal, Form, Input, InputNumber, DatePicker, message } from 'antd'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { backtestAPI } from '../../services/api'
import type { BacktestRequest } from '../../types/api'
import dayjs from 'dayjs'

interface BacktestModalProps {
  visible: boolean
  strategyId: string
  onClose: () => void
}

const BacktestModal: React.FC<BacktestModalProps> = ({ visible, strategyId, onClose }) => {
  const [form] = Form.useForm()
  const navigate = useNavigate()

  const backtestMutation = useMutation({
    mutationFn: (data: BacktestRequest) => backtestAPI.run(data),
    onSuccess: (data) => {
      message.success('回测启动成功')
      onClose()
      form.resetFields()
      navigate(`/backtest/${data.id}`)
    },
    onError: (error: Error) => {
      message.error(`回测失败: ${error.message}`)
    },
  })

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const request: BacktestRequest = {
        strategy_id: strategyId,
        stock_code: values.stock_code,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD'),
        initial_capital: values.initial_capital,
        commission_rate: values.commission_rate,
      }
      backtestMutation.mutate(request)
    } catch (error) {
      console.error('Validation failed:', error)
    }
  }

  return (
    <Modal
      title="运行回测"
      open={visible}
      onOk={handleSubmit}
      onCancel={onClose}
      confirmLoading={backtestMutation.isPending}
      width={600}
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="stock_code"
          label="股票代码"
          rules={[{ required: true, message: '请输入股票代码' }]}
        >
          <Input placeholder="例如: 000001" />
        </Form.Item>
        <Form.Item
          name="dateRange"
          label="回测日期范围"
          rules={[
            { required: true, message: '请选择日期范围' },
            {
              validator: (_, value) => {
                if (!value || !value[0] || !value[1]) {
                  return Promise.resolve()
                }
                const today = dayjs()
                const startDate = value[0]
                const endDate = value[1]
                
                if (endDate.isAfter(today)) {
                  return Promise.reject(new Error('结束日期不能是未来日期，请选择历史日期'))
                }
                if (startDate.isAfter(endDate)) {
                  return Promise.reject(new Error('开始日期不能晚于结束日期'))
                }
                return Promise.resolve()
              },
            },
          ]}
        >
          <DatePicker.RangePicker
            style={{ width: '100%' }}
            disabledDate={(current) => {
              // 禁用未来日期
              return current && current > dayjs().endOf('day')
            }}
            placeholder={['开始日期', '结束日期']}
          />
        </Form.Item>
        <Form.Item
          name="initial_capital"
          label="初始资金"
          initialValue={1000000}
          rules={[{ required: true, message: '请输入初始资金' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={10000}
            formatter={(value) => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
            parser={(value) => value!.replace(/¥\s?|(,*)/g, '')}
          />
        </Form.Item>
        <Form.Item
          name="commission_rate"
          label="手续费率"
          initialValue={0.0003}
          rules={[{ required: true, message: '请输入手续费率' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0}
            max={0.01}
            step={0.0001}
            formatter={(value) => `${(value! * 100).toFixed(4)}%`}
            parser={(value) => parseFloat(value!.replace('%', '')) / 100}
          />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default BacktestModal

