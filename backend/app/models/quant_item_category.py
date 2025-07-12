from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class QuantItemCategory(Base):
    __tablename__ = "quant_item_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, comment="分类名称")
    description = Column(Text, nullable=True, comment="分类描述")
    order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 关系
    items = relationship("QuantItem", back_populates="category_rel") 