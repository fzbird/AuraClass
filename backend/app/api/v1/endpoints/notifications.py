from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.models.user import User
from app.crud.notification import notification as notification_crud
from app.schemas.notification import (
    Notification, NotificationCreate, NotificationUpdate,
    NotificationList
)
from app.websockets.connection import notification_manager

router = APIRouter()

@router.get("/", response_model=NotificationList)
async def read_notifications(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    unread_only: bool = Query(False),
    search: Optional[str] = Query(None, description="搜索通知标题和内容"),
    current_user: User = require_permissions(path="/api/v1/notifications", method="GET")
) -> Any:
    """
    获取用户的通知列表
    
    可选参数:
    - skip: 分页偏移量 
    - limit: 每页数量
    - unread_only: 是否只返回未读通知
    - search: 搜索标题和内容
    """
    notifications = await notification_crud.get_user_notifications(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        search=search
    )
    
    # 处理数据，确保字段一致性
    notification_list = []
    for notification in notifications:
        notification_dict = {
            "id": notification.id,
            "title": notification.title,
            "content": notification.content,
            "notification_type": notification.notification_type,
            "recipient_user_id": notification.recipient_user_id,
            "recipient_role_id": notification.recipient_role_id,
            "sender_id": notification.sender_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
            "sender_name": notification.sender.full_name if hasattr(notification, "sender") and notification.sender else None,
            "recipient_name": notification.recipient_user.full_name if hasattr(notification, "recipient_user") and notification.recipient_user else None
        }
        notification_list.append(notification_dict)
    
    return {
        "data": notification_list,
        "meta": {
            "count": len(notification_list),
            "unread_count": sum(1 for n in notification_list if not n["is_read"])
        }
    }

@router.post("/", response_model=Notification)
async def create_notification(
    *,
    db: AsyncSession = Depends(get_db),
    notification_in: NotificationCreate,
    current_user: User = require_permissions(path="/api/v1/notifications", method="POST")
) -> Any:
    """
    创建新通知
    """
    # 验证角色 ID 和用户 ID
    if notification_in.recipient_role_id is not None and notification_in.recipient_role_id == 0:
        notification_in.recipient_role_id = None
    
    if notification_in.recipient_user_id is not None and notification_in.recipient_user_id == 0:
        notification_in.recipient_user_id = None
        
    # 设置发送者
    notification_in.sender_id = current_user.id
    
    # 如果同时都为 None，则设置为系统通知
    if notification_in.recipient_role_id is None and notification_in.recipient_user_id is None:
        # 系统广播通知
        pass
    
    # 发送通知
    notification = await notification_manager.send_notification(
        db,
        notification_in,
        exclude_sender=True
    )
    
    if not notification:
        raise HTTPException(
            status_code=500,
            detail="发送通知失败"
        )
    
    # 处理数据，确保字段一致性
    notification_dict = {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "notification_type": notification.notification_type,
        "recipient_user_id": notification.recipient_user_id,
        "recipient_role_id": notification.recipient_role_id,
        "sender_id": notification.sender_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "read_at": notification.read_at,
        "sender_name": current_user.full_name,
        "recipient_name": None
    }
    
    return notification_dict

@router.get("/{notification_id}", response_model=Notification)
async def read_notification(
    *,
    db: AsyncSession = Depends(get_db),
    notification_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/notifications/{notification_id}", method="GET")
) -> Any:
    """
    获取指定通知详情
    """
    notification = await notification_crud.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="通知不存在"
        )
    
    # 检查用户是否有权限查看通知
    if (notification.recipient_user_id and notification.recipient_user_id != current_user.id) and \
       (notification.recipient_role_id and notification.recipient_role_id != current_user.role_id):
        raise HTTPException(
            status_code=403,
            detail="无权访问该通知"
        )
    
    # 处理数据，确保字段一致性
    notification_dict = {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "notification_type": notification.notification_type,
        "recipient_user_id": notification.recipient_user_id,
        "recipient_role_id": notification.recipient_role_id,
        "sender_id": notification.sender_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "read_at": notification.read_at,
        "sender_name": notification.sender.full_name if hasattr(notification, "sender") and notification.sender else None,
        "recipient_name": notification.recipient_user.full_name if hasattr(notification, "recipient_user") and notification.recipient_user else None
    }
    
    return notification_dict

@router.patch("/{notification_id}/read", response_model=Notification)
async def mark_notification_as_read(
    *,
    db: AsyncSession = Depends(get_db),
    notification_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/notifications/{notification_id}/read", method="PATCH")
) -> Any:
    """
    将通知标记为已读
    """
    notification = await notification_crud.mark_as_read(
        db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="通知不存在或无权访问"
        )
    
    # 处理数据，确保字段一致性
    notification_dict = {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "notification_type": notification.notification_type,
        "recipient_user_id": notification.recipient_user_id,
        "recipient_role_id": notification.recipient_role_id,
        "sender_id": notification.sender_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "read_at": notification.read_at,
        "sender_name": notification.sender.full_name if hasattr(notification, "sender") and notification.sender else None,
        "recipient_name": notification.recipient_user.full_name if hasattr(notification, "recipient_user") and notification.recipient_user else None
    }
    
    return notification_dict

@router.patch("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/notifications/read-all", method="PATCH")
) -> Any:
    """
    将所有通知标记为已读
    """
    updated_count = await notification_crud.mark_all_as_read(
        db,
        user_id=current_user.id
    )
    
    return {
        "message": f"已将{updated_count}条通知标记为已读",
        "updated_count": updated_count
    }

@router.delete("/{id}", response_model=Notification)
async def delete_notification(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = require_permissions(path="/api/v1/notifications/{id}", method="DELETE")
) -> Any:
    """
    删除通知.
    
    权限规则：
    1. 管理员可以删除所有通知
    2. 接收者可以删除发给他个人的通知
    3. 发送者可以删除他自己发布的所有未读通知（已读通知不能删除）
    """
    try:
        # 获取通知
        notification = await notification_crud.get(db=db, id=id)
        if not notification:
            raise HTTPException(status_code=404, detail="通知不存在")
        
        # 检查权限
        is_admin = current_user.role and current_user.role.name.lower() == "admin"
        is_recipient = notification.recipient_user_id == current_user.id
        is_sender = notification.sender_id == current_user.id
        is_unread = not notification.is_read
        
        # 权限检查逻辑实现
        has_permission = False
        
        # 规则1: 管理员可以删除所有通知
        if is_admin:
            has_permission = True
        # 规则2: 接收者可以删除发给他个人的通知
        elif is_recipient:
            has_permission = True
        # 规则3: 发送者可以删除自己发布的未读通知
        elif is_sender and is_unread:
            has_permission = True
        
        if not has_permission:
            # 提供清晰的错误消息，解释为什么无法删除
            if is_sender and not is_unread:
                raise HTTPException(status_code=403, detail="无法删除已读通知")
            else:
                raise HTTPException(status_code=403, detail="无权删除此通知")
        
        # 使用事务保证删除操作的完整性
        try:
            # 删除通知
            deleted_notification = await notification_crud.remove(db=db, id=id)
            
            # 处理数据，确保字段一致性
            result = {
                "id": deleted_notification.id,
                "title": deleted_notification.title,
                "content": deleted_notification.content,
                "notification_type": deleted_notification.notification_type,
                "recipient_user_id": deleted_notification.recipient_user_id,
                "recipient_role_id": deleted_notification.recipient_role_id,
                "sender_id": deleted_notification.sender_id,
                "is_read": deleted_notification.is_read,
                "created_at": deleted_notification.created_at,
                "read_at": deleted_notification.read_at,
                "sender_name": deleted_notification.sender.full_name if hasattr(deleted_notification, "sender") and deleted_notification.sender else None,
                "recipient_name": deleted_notification.recipient_user.full_name if hasattr(deleted_notification, "recipient_user") and deleted_notification.recipient_user else None
            }
            
            return result
        except Exception as e:
            # 事务回滚已由FastAPI自动处理
            raise HTTPException(
                status_code=500,
                detail=f"删除通知时发生错误: {str(e)}"
            )
    except HTTPException:
        # 直接重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他未预期的异常
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )
