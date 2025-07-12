from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, func, Index, Boolean, Float
from sqlalchemy.orm import relationship

from app.db.base import Base  # 从正确的文件导入Base
from app.models.uploads import Upload  # 导入Upload模型

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    title = Column(String(255), nullable=False, default="未命名对话", comment="对话标题")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("ix_ai_conversations_user_id_updated_at", "user_id", "updated_at"),
    )


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False, comment="对话ID")
    role = Column(String(50), nullable=False, comment="消息角色，user或assistant")
    content = Column(Text, nullable=False, comment="消息内容")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    processing_time = Column(Float, nullable=True, comment="处理时间（秒）（仅适用于assistant消息）")
    use_local_model = Column(Boolean, default=True, nullable=True, comment="是否使用本地模型")
    model_name = Column(String(100), default="gemma3:27", nullable=True, comment="使用的模型名称")
    
    # 关系
    conversation = relationship("AIConversation", back_populates="messages")
    
    # 索引
    __table_args__ = (
        Index("ix_ai_messages_conversation_id_created_at", "conversation_id", "created_at"),
    )
    
    @property
    def get_attachments(self):
        """获取关联到此消息的附件，需要在ORM会话中使用"""
        pass 