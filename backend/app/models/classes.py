from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class Classes(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="班级名称")
    grade = Column(String(20), nullable=False, comment="年级")
    year = Column(Integer, nullable=False, comment="入学年份")
    head_teacher_id = Column(Integer, ForeignKey("users.id", use_alter=True, name="fk_classes_head_teacher_id"), nullable=True, comment="班主任ID")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    head_teacher = relationship(
        "User", 
        foreign_keys=[head_teacher_id],
        back_populates="managed_class"
    )
    users = relationship("User", back_populates="class_", foreign_keys="User.class_id")
    students = relationship("Student", back_populates="class_")
