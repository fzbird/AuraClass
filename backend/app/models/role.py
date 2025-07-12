from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    name = Column(String(50), unique=True, nullable=False, index=True, comment="名称")
    description = Column(String(255), nullable=True, comment="描述")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")

    # 关系
    users = relationship("User", back_populates="role")
    notifications = relationship("Notification", back_populates="recipient_role")
