from typing import List, Optional
from datetime import timezone, datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate

class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    async def get_user_notifications(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False,
        search: Optional[str] = None
    ) -> List[Notification]:
        """
        获取用户的通知
        
        参数:
        - user_id: 用户ID
        - skip: 分页偏移
        - limit: 限制返回数量
        - unread_only: 是否只返回未读通知
        - search: 搜索关键词（搜索标题和内容）
        """
        conditions = [
            or_(
                Notification.recipient_user_id == user_id,
                and_(
                    Notification.recipient_role_id.in_(
                        select(User.role_id).where(User.id == user_id)
                    ),
                    Notification.recipient_user_id.is_(None)
                ),
                and_(
                    Notification.recipient_user_id.is_(None),
                    Notification.recipient_role_id.is_(None)
                )
            )
        ]
        
        if unread_only:
            conditions.append(Notification.is_read.is_(False))
        
        # 添加搜索条件
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Notification.title.ilike(search_term),
                    Notification.content.ilike(search_term)
                )
            )
        
        query = (
            select(Notification)
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()

    async def mark_as_read(
        self,
        db: AsyncSession,
        *,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """将通知标记为已读"""
        notification = await self.get(db, id=notification_id)
        if notification and (
            notification.recipient_user_id == user_id or
            notification.recipient_user_id is None
        ):
            notification_in = NotificationUpdate(
                is_read=True,
                read_at=datetime.now(timezone.utc)
            )
            return await self.update(db, db_obj=notification, obj_in=notification_in)
        return None

    async def mark_all_as_read(
        self,
        db: AsyncSession,
        *,
        user_id: int
    ) -> int:
        """将用户的所有通知标记为已读"""
        conditions = [
            or_(
                Notification.recipient_user_id == user_id,
                and_(
                    Notification.recipient_role_id.in_(
                        select(User.role_id).where(User.id == user_id)
                    ),
                    Notification.recipient_user_id.is_(None)
                ),
                and_(
                    Notification.recipient_user_id.is_(None),
                    Notification.recipient_role_id.is_(None)
                )
            ),
            Notification.is_read.is_(False)
        ]
        
        query = (
            select(Notification)
            .where(and_(*conditions))
        )
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        
        await db.commit()
        return len(notifications)

# 创建全局通知CRUD实例
notification = CRUDNotification(Notification)
