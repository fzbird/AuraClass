from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Upload(Base):
    """通用文件上传模型，用于存储上传文件的元数据"""
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, comment="文件名")
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(512), nullable=False, comment="文件路径")
    file_type = Column(String(100), nullable=False, comment="文件MIME类型")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    module = Column(String(50), nullable=False, comment="所属模块，如ai-assistant, profile, etc.")
    entity_type = Column(String(50), nullable=True, comment="实体类型，如message, user, etc.")
    entity_id = Column(Integer, nullable=True, comment="关联实体ID")
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传者ID")
    is_public = Column(Integer, default=0, nullable=False, comment="是否公开，0-私有，1-公开")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 关系
    uploader = relationship("User", foreign_keys=[uploader_id])
    
    # 索引
    __table_args__ = (
        Index("ix_uploads_entity_type_entity_id", "entity_type", "entity_id"),
        Index("ix_uploads_uploader_id", "uploader_id"),
        Index("ix_uploads_module", "module"),
    ) 