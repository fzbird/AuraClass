from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, func, Boolean, Float
from sqlalchemy.orm import relationship

from app.db.base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="用户ID")
    student_id_no = Column(String(50), unique=True, nullable=False, index=True, comment="学号")
    full_name = Column(String(100), nullable=False, index=True, comment="姓名")
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True, index=True, comment="班级ID")
    gender = Column(String(10), nullable=False, comment="性别")
    phone = Column(String(20), nullable=True, comment="电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    birth_date = Column(Date, nullable=True, comment="出生日期")
    contact_info = Column(String(255), nullable=True, comment="联系方式")
    avatar_url = Column(String(255), nullable=True, comment="头像URL")
    total_score = Column(Float, nullable=True, default=0.0, comment="总分")
    rank = Column(Integer, nullable=True, comment="排名")
    is_active = Column(Boolean, nullable=False, default=True, comment="是否激活")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", foreign_keys=[user_id])
    class_ = relationship("Classes", back_populates="students")
    quant_records = relationship("QuantRecord", back_populates="student")
