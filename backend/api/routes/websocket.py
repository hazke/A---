"""
WebSocket路由 - 实时数据推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.observer.observer import MarketDataSubject, LoggingObserver
from core.factory.data_factory import DataFactory

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.market_subject = MarketDataSubject()
        self.logging_observer = LoggingObserver()
        self.market_subject.attach(self.logging_observer)
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # 移除断开的连接
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


class WebSocketObserver:
    """WebSocket观察者，将市场数据推送到前端"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
    
    async def update(self, event_type: str, data: dict):
        """接收事件并推送到前端"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": data.get("timestamp").isoformat() if "timestamp" in data else None
        }
        await self.manager.broadcast(message)


@router.websocket("/market")
async def websocket_market(websocket: WebSocket):
    """实时行情WebSocket"""
    await manager.connect(websocket)
    
    # 添加WebSocket观察者
    ws_observer = WebSocketObserver(manager)
    manager.market_subject.attach(ws_observer)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理订阅请求
            if message.get("action") == "subscribe":
                stock_code = message.get("stock_code")
                if stock_code:
                    # 这里可以启动实时数据推送任务
                    await websocket.send_json({
                        "type": "subscribed",
                        "stock_code": stock_code
                    })
            
            # 处理取消订阅
            elif message.get("action") == "unsubscribe":
                await websocket.send_json({
                    "type": "unsubscribed"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        manager.market_subject.detach(ws_observer)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """通用WebSocket端点"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

