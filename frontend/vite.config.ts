import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 检测是否在Docker环境中
// 在Docker中，Vite代理应该指向Docker网络中的后端服务
const isDocker = process.env.DOCKER === 'true'
// Docker环境中使用服务名，本地开发使用localhost
const backendUrl = isDocker ? 'http://backend:8000' : 'http://localhost:8000'
const backendWsUrl = isDocker ? 'ws://backend:8000' : 'ws://localhost:8000'

console.log('Vite配置:', {
  isDocker,
  backendUrl,
  backendWsUrl,
  NODE_ENV: process.env.NODE_ENV
})

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0', // 允许外部访问（Docker需要）
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('[代理错误]', err.message)
            console.error('[代理错误详情]', {
              code: err.code,
              address: err.address,
              port: err.port
            })
          })
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log(`[代理请求] ${req.method} ${req.url} -> ${backendUrl}${req.url}`)
          })
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log(`[代理响应] ${req.method} ${req.url} -> ${proxyRes.statusCode}`)
          })
        },
      },
      '/ws': {
        target: backendWsUrl,
        ws: true,
        changeOrigin: true,
      },
    },
  },
})

