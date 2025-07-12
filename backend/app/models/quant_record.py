from sqlalchemy import Column, ForeignKey, Integer, Numeric, Text, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class QuantRecord(Base):
    __tablename__ = "quant_records"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True, comment="学生ID")
    item_id = Column(Integer, ForeignKey("quant_items.id"), nullable=False, index=True, comment="项目ID")
    score = Column(Numeric(5, 2), nullable=False, comment="分数")
    reason = Column(Text, nullable=True, comment="原因")
    recorder_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="记录者ID")
    record_date = Column(Date, nullable=False, index=True, comment="记录日期")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="quant_records")
    item = relationship("QuantItem", back_populates="quant_records")
    recorder = relationship("User", back_populates="quant_records_created")
