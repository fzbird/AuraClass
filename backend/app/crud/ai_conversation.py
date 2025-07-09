from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.ai_conversation import AIConversation, AIMessage
from app.schemas.ai_conversation import ConversationCreate, ConversationUpdate, MessageCreate

class CRUDConversation(CRUDBase[AIConversation, ConversationCreate, ConversationUpdate]):
    async def get_user_conversations(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[AIConversation]:
        """获取用户的所有对话，按更新时间降序排序"""
        query = (
            select(AIConversation)
            .where(AIConversation.user_id == user_id)
            .order_by(AIConversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_conversation(
        self, db: AsyncSession, *, obj_in: ConversationCreate, user_id: int
    ) -> AIConversation:
        """创建新对话"""
        db_obj = AIConversation(
            user_id=user_id,
            title=obj_in.title or "未命名对话",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_conversation_with_messages(
        self, db: AsyncSession, *, conversation_id: int, user_id: Optional[int] = None
    ) -> Optional[AIConversation]:
        """获取对话及其消息"""
        query = (
            select(AIConversation)
            .options(selectinload(AIConversation.messages))
            .where(AIConversation.id == conversation_id)
        )
        
        if user_id is not None:
            query = query.where(AIConversation.user_id == user_id)
            
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_conversation_title(
        self, db: AsyncSession, *, conversation_id: int, title: str, user_id: Optional[int] = None
    ) -> Optional[AIConversation]:
        """更新对话标题"""
        query = update(AIConversation).where(AIConversation.id == conversation_id)
        
        if user_id is not None:
            query = query.where(AIConversation.user_id == user_id)
            
        query = query.values(title=title, updated_at=datetime.utcnow())
        await db.execute(query)
        await db.commit()
        
        return await self.get(db, id=conversation_id)
    
    async def touch_conversation(
        self, db: AsyncSession, *, conversation_id: int
    ) -> None:
        """更新对话的更新时间"""
        query = (
            update(AIConversation)
            .where(AIConversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )
        await db.execute(query)
        await db.commit()
    
    async def delete_conversation(
        self, db: AsyncSession, *, conversation_id: int, user_id: Optional[int] = None
    ) -> bool:
        """删除对话"""
        query = delete(AIConversation).where(AIConversation.id == conversation_id)
        
        if user_id is not None:
            query = query.where(AIConversation.user_id == user_id)
            
        result = await db.execute(query)
        await db.commit()
        
        return result.rowcount > 0


class CRUDMessage(CRUDBase[AIMessage, MessageCreate, MessageCreate]):
    async def create_message(
        self, db: AsyncSession, *, conversation_id: int, obj_in: MessageCreate
    ) -> AIMessage:
        """创建新消息"""
        db_obj = AIMessage(
            conversation_id=conversation_id,
            role=obj_in.role,
            content=obj_in.content,
            created_at=datetime.utcnow(),
            use_local_model=obj_in.useLocalModel if hasattr(obj_in, "useLocalModel") else True,
            model_name=obj_in.modelName if hasattr(obj_in, "modelName") else "gemma3:27b",
            processing_time=obj_in.processingTime if hasattr(obj_in, "processingTime") else None
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_conversation_messages(
        self, db: AsyncSession, *, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> List[AIMessage]:
        """获取对话的所有消息，按创建时间升序排序"""
        query = (
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_newest_message(
        self, db: AsyncSession, *, conversation_id: int, role: Optional[str] = None
    ) -> Optional[AIMessage]:
        """获取对话中最新的消息，可以按角色筛选"""
        query = (
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
        )
        
        # 如果指定了角色，添加角色筛选条件
        if role:
            query = query.where(AIMessage.role == role)
            
        # 按创建时间降序排序，限制返回1条
        query = query.order_by(AIMessage.created_at.desc()).limit(1)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def count_messages(
        self, db: AsyncSession, *, conversation_id: int
    ) -> int:
        """统计对话中的消息数量"""
        query = (
            select(func.count(AIMessage.id))
            .where(AIMessage.conversation_id == conversation_id)
        )
        result = await db.execute(query)
        return result.scalar_one() or 0
    
    async def delete_message(
        self, db: AsyncSession, *, message_id: int, conversation_id: Optional[int] = None
    ) -> bool:
        """删除指定消息"""
        query = delete(AIMessage).where(AIMessage.id == message_id)
        
        if conversation_id is not None:
            query = query.where(AIMessage.conversation_id == conversation_id)
            
        result = await db.execute(query)
        await db.commit()
        
        return result.rowcount > 0


conversation = CRUDConversation(AIConversation)
message = CRUDMessage(AIMessage) 