from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    notification_type = Column(String(50), nullable=False, comment="类型")  # system, role, personal
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="发送者ID")
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="接收者用户ID")
    recipient_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, comment="接收者角色ID")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    read_at = Column(DateTime, nullable=True, comment="阅读时间")

    # 关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="notifications_sent")
    recipient_user = relationship("User", foreign_keys=[recipient_user_id], back_populates="notifications_received")
    recipient_role = relationship("Role", back_populates="notifications")
