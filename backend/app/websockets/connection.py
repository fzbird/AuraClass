from typing import Dict, List, Optional, Set
from datetime import datetime
import json
import asyncio
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.crud.notification import notification as notification_crud
from app.schemas.notification import NotificationCreate, Notification
from app.core.logging import get_logger

logger = get_logger(__name__)

# 自定义JSON编码器，处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ConnectionManager:
    def __init__(self):
        # 存储活跃连接，按用户ID分组
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # 存储用户角色映射
        self.user_roles: Dict[int, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, user_roles: Set[int]):
        """建立新的WebSocket连接"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.user_roles[user_id] = user_roles
        logger.info(f"User {user_id} connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                del self.user_roles[user_id]
        logger.info(f"User {user_id} disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, user_id: int, message: dict):
        """发送个人消息"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    # 使用自定义编码器序列化JSON
                    json_str = json.dumps(message, cls=DateTimeEncoder)
                    await websocket.send_text(json_str)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")
                    disconnected.append(websocket)
            
            # 清理断开的连接
            for websocket in disconnected:
                self.disconnect(websocket, user_id)

    async def send_role_message(self, role_id: int, message: dict):
        """发送角色消息"""
        for user_id, roles in self.user_roles.items():
            if role_id in roles:
                await self.send_personal_message(user_id, message)

    async def broadcast(self, message: dict):
        """广播消息给所有连接的用户"""
        disconnected_users = []
        for user_id in self.active_connections:
            try:
                await self.send_personal_message(user_id, message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
                del self.user_roles[user_id]

    async def send_notification(
        self, 
        db: AsyncSession,
        notification: NotificationCreate,
        exclude_sender: bool = True
    ):
        """发送通知并保存到数据库"""
        try:
            # 创建通知记录
            db_notification = await notification_crud.create(db, obj_in=notification)
            
            # 构造WebSocket消息
            message = {
                "type": "notification",
                "data": {
                    "id": db_notification.id,
                    "title": db_notification.title,
                    "content": db_notification.content,
                    "notification_type": db_notification.notification_type,
                    "created_at": db_notification.created_at.isoformat() if db_notification.created_at else None
                }
            }
            
            # 发送通知
            try:
                if notification.recipient_user_id:
                    # 个人通知
                    if not exclude_sender or notification.sender_id != notification.recipient_user_id:
                        await self.send_personal_message(notification.recipient_user_id, message)
                elif notification.recipient_role_id:
                    # 角色通知
                    await self.send_role_message(notification.recipient_role_id, message)
                else:
                    # 广播通知
                    await self.broadcast(message)
            except Exception as e:
                print(f"WebSocket通知发送失败: {str(e)}")
                # 通知已创建，即使WebSocket发送失败也返回成功
                
            return db_notification
        except Exception as e:
            print(f"发送通知失败: {str(e)}")
            return None

# 创建全局连接管理器实例
notification_manager = ConnectionManager()
