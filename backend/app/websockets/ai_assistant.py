from typing import Dict, Set, Optional
from datetime import datetime, timezone
import json
import asyncio

from fastapi import WebSocket, APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.ai_service import ai_assistant
from app.core.logging import get_logger

logger = get_logger(__name__)

# 自定义JSON编码器，处理datetime对象
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class AIAssistantConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_sessions: Dict[int, dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """建立新的WebSocket连接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            "last_query_time": datetime.now(timezone.utc),
            "query_count": 0
        }
        logger.info(f"AI Assistant: User {user_id} connected")
    
    def disconnect(self, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"AI Assistant: User {user_id} disconnected")
    
    async def send_response(self, user_id: int, message: dict):
        """发送AI响应"""
        if user_id in self.active_connections:
            try:
                # 使用自定义编码器序列化JSON
                json_str = json.dumps(message, cls=DateTimeEncoder)
                await self.active_connections[user_id].send_text(json_str)
            except Exception as e:
                logger.error(f"Error sending AI response to user {user_id}: {str(e)}")
                self.disconnect(user_id)

# 创建全局AI助手连接管理器实例
ai_connection_manager = AIAssistantConnectionManager()

router = APIRouter()

async def get_token_data(token: str) -> TokenPayload:
    """验证WebSocket连接的token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        return token_data
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

@router.websocket("/ws/ai-assistant/{user_id}")
async def websocket_ai_assistant(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """AI助手WebSocket端点"""
    logger.info(f"尝试建立AI助手WebSocket连接: user_id={user_id}")
    try:
        # 验证token
        token_data = await get_token_data(token)
        print(token_data,user_id)

        # 验证用户身份匹配
        if str(user_id) != token_data.sub:
            logger.warning(f"AI助手WebSocket连接用户身份不匹配: token_sub={token_data.sub}, user_id={user_id}")
            await websocket.close(code=1008)  # Policy Violation
            return
        
        # 获取用户信息
        user = await get_current_user(db, token)
        if not user or not user.is_active:
            logger.warning(f"AI助手WebSocket连接用户不存在或未激活: user_id={user_id}")
            await websocket.close(code=1008)
            return
        
        # 获取用户角色
        user_roles = {user.role_id}  # 实际项目中可能需要获取更多角色
      
        # 建立WebSocket连接
        await ai_connection_manager.connect(websocket, user_id)
        logger.info(f"AI助手WebSocket连接建立成功: user_id={user_id}")
        
        try:
            while True:
                # 接收用户消息
                data = await websocket.receive_json()
                
                if data.get("type") == "query":
                    # 处理AI查询
                    query_text = data.get("data", {}).get("query_text")
                    context_data = data.get("data", {}).get("context_data")
                    
                    if query_text:
                        # 处理查询
                        result = await ai_assistant.process_query(
                            db,
                            user_id=user_id,
                            query_text=query_text,
                            context_data=context_data
                        )
                        
                        # 发送响应
                        await ai_connection_manager.send_response(
                            user_id,
                            {
                                "type": "response",
                                "data": result
                            }
                        )
                
                elif data.get("type") == "suggest":
                    # 处理建议请求
                    prefix = data.get("data", {}).get("prefix", "")
                    suggestions = await ai_assistant.get_suggestions(
                        db,
                        user_id=user_id,
                        prefix=prefix
                    )
                    
                    # 发送建议
                    await ai_connection_manager.send_response(
                        user_id,
                        {
                            "type": "suggestions",
                            "data": {
                                "suggestions": suggestions
                            }
                        }
                    )
                
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {str(e)}")
            ai_connection_manager.disconnect(user_id)
            
    except Exception as e:
        logger.error(f"Error in AI assistant WebSocket connection: {str(e)}")
        await websocket.close(code=1011)
