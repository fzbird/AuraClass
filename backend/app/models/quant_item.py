from sqlalchemy import Boolean, Column, Integer, String, Text, Numeric, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class QuantItem(Base):
    __tablename__ = "quant_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="名称")
    description = Column(Text, nullable=True, comment="描述")
    min_score = Column(Numeric(5, 2), nullable=False, comment="最小分数")
    max_score = Column(Numeric(5, 2), nullable=False, comment="最大分数")
    default_score = Column(Numeric(5, 2), nullable=True, comment="默认分数")
    default_reason = Column(Text, nullable=True, comment="默认原因")
    weight = Column(Numeric(5, 2), default=1.0, nullable=False, comment="权重")
    category = Column(String(50), nullable=False, comment="类别")
    category_id = Column(Integer, ForeignKey("quant_item_categories.id"), nullable=True, comment="分类ID")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    quant_records = relationship("QuantRecord", back_populates="item")
    category_rel = relationship("QuantItemCategory", back_populates="items")
