from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), nullable=False, comment="姓名")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True, comment="班级ID")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    role = relationship("Role", back_populates="users", lazy="joined")
    class_ = relationship("Classes", back_populates="users", foreign_keys=[class_id], post_update=True)
    managed_class = relationship("Classes", back_populates="head_teacher", foreign_keys="Classes.head_teacher_id")
    quant_records_created = relationship("QuantRecord", back_populates="recorder")
    notifications_sent = relationship(
        "Notification", 
        back_populates="sender", 
        foreign_keys="Notification.sender_id"
    )
    notifications_received = relationship(
        "Notification", 
        back_populates="recipient_user", 
        foreign_keys="Notification.recipient_user_id"
    )
    ai_conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
