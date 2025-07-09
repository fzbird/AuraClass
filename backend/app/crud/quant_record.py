from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.quant_record import QuantRecord
from app.models.student import Student
from app.models.quant_item import QuantItem
from app.models.user import User
from app.models.classes import Classes
from app.schemas.quant_record import QuantRecordCreate, QuantRecordUpdate

class CRUDQuantRecord(CRUDBase[QuantRecord, QuantRecordCreate, QuantRecordUpdate]):
    async def create_with_recorder(
        self, db: AsyncSession, *, obj_in: QuantRecordCreate, recorder_id: int
    ) -> QuantRecord:
        """创建量化记录，指定记录者"""
        obj_in_data = obj_in.dict()
        obj_in_data["recorder_id"] = recorder_id
        db_obj = QuantRecord(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def create_batch(
        self, db: AsyncSession, *, obj_in_list: List[QuantRecordCreate]
    ) -> int:
        """批量创建量化记录"""
        db_objs = [QuantRecord(**obj_in.dict()) for obj_in in obj_in_list]
        db.add_all(db_objs)
        await db.commit()
        return len(db_objs)
    
    async def get_by_student(
        self, db: AsyncSession, *, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Tuple[QuantRecord, Student, QuantItem, User]]:
        """获取学生的量化记录"""
        query = (
            select(QuantRecord, Student, QuantItem, User)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .where(QuantRecord.student_id == student_id)
            .order_by(QuantRecord.record_date.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.all()
    
    async def get_by_item(
        self, db: AsyncSession, *, item_id: int, skip: int = 0, limit: int = 100
    ) -> List[Tuple[QuantRecord, Student, QuantItem, User]]:
        """获取量化项目的记录"""
        query = (
            select(QuantRecord, Student, QuantItem, User)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .where(QuantRecord.item_id == item_id)
            .order_by(QuantRecord.record_date.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.all()
    
    async def get_by_date_range(
        self, db: AsyncSession, *, start_date: date, end_date: date,
        student_id: Optional[int] = None, item_id: Optional[int] = None,
        skip: int = 0, limit: int = 100
    ) -> List[Tuple[QuantRecord, Student, QuantItem, User]]:
        """获取日期范围内的记录"""
        conditions = [
            QuantRecord.record_date >= start_date,
            QuantRecord.record_date <= end_date
        ]
        
        if student_id:
            conditions.append(QuantRecord.student_id == student_id)
        
        if item_id:
            conditions.append(QuantRecord.item_id == item_id)
        
        query = (
            select(QuantRecord, Student, QuantItem, User)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .where(and_(*conditions))
            .order_by(QuantRecord.record_date.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.all()
    
    async def get_record_with_details(
        self, db: AsyncSession, *, record_id: int
    ) -> Optional[Tuple[QuantRecord, Student, QuantItem, User, Optional[Classes]]]:
        """获取带详细信息的量化记录"""
        query = (
            select(QuantRecord, Student, QuantItem, User, Classes)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .outerjoin(Classes, Student.class_id == Classes.id)
            .where(QuantRecord.id == record_id)
        )
        result = await db.execute(query)
        return result.first()
    
    async def get_by_student_and_item(
        self, db: AsyncSession, *, student_id: int, item_id: int, skip: int = 0, limit: int = 100
    ) -> List[Tuple[QuantRecord, Student, QuantItem, User]]:
        """获取指定学生和项目的量化记录"""
        query = (
            select(QuantRecord, Student, QuantItem, User)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .where(
                and_(
                    QuantRecord.student_id == student_id,
                    QuantRecord.item_id == item_id
                )
            )
            .order_by(QuantRecord.record_date.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(query)
        return result.all()
    
    async def get_multi_with_details(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100,
        student_id: Optional[int] = None, item_id: Optional[int] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Tuple[QuantRecord, Student, QuantItem, User, Optional[Classes]]]:
        """获取带详细信息的量化记录列表，包含班级信息"""
        conditions = []
        
        if student_id:
            conditions.append(QuantRecord.student_id == student_id)
        
        if item_id:
            conditions.append(QuantRecord.item_id == item_id)
        
        if start_date:
            conditions.append(QuantRecord.record_date >= start_date)
        
        if end_date:
            conditions.append(QuantRecord.record_date <= end_date)
        
        # 主查询，包含班级信息
        query = (
            select(QuantRecord, Student, QuantItem, User, Classes)
            .join(Student, QuantRecord.student_id == Student.id)
            .join(QuantItem, QuantRecord.item_id == QuantItem.id)
            .join(User, QuantRecord.recorder_id == User.id)
            .outerjoin(Classes, Student.class_id == Classes.id)
        )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(QuantRecord.record_date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.all()

# 创建全局量化记录CRUD实例
quant_record_crud = CRUDQuantRecord(QuantRecord)
