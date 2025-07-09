from typing import Optional, Set
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.websockets.connection import notification_manager
from app.crud.notification import notification as notification_crud
from app.core.logging import get_logger

logger = get_logger(__name__)

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

@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket通知端点"""
    logger.info(f"尝试建立WebSocket通知连接: user_id={user_id}")
    try:
        # 验证token
        token_data = await get_token_data(token)
        print(token_data,user_id)

        # 验证用户身份匹配
        if str(user_id) != token_data.sub:
            logger.warning(f"WebSocket通知连接用户身份不匹配: token_sub={token_data.sub}, user_id={user_id}")
            await websocket.close(code=1008)  # Policy Violation
            return
        
        # 获取用户信息
        user = await get_current_user(db, token)
        if not user or not user.is_active:
            logger.warning(f"WebSocket通知连接用户不存在或未激活: user_id={user_id}")
            await websocket.close(code=1008)
            return
        
        # 获取用户角色
        user_roles = {user.role_id}  # 实际项目中可能需要获取更多角色
        
        # 建立WebSocket连接
        await notification_manager.connect(websocket, user_id, user_roles)
        logger.info(f"WebSocket通知连接建立成功: user_id={user_id}, roles={user_roles}")
        
        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_json()
                
                # 处理消息确认
                if data.get("type") == "ack" and "notification_id" in data:
                    await notification_crud.mark_as_read(
                        db,
                        notification_id=data["notification_id"],
                        user_id=user_id
                    )
        except WebSocketDisconnect:
            notification_manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {str(e)}")
            notification_manager.disconnect(websocket, user_id)
            
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
        await websocket.close(code=1011)  # Internal Error
