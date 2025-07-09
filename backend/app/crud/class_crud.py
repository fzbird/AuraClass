from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.classes import Classes
from app.schemas.class_schema import ClassCreate, ClassUpdate

class CRUDClass(CRUDBase[Classes, ClassCreate, ClassUpdate]):
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Classes]:
        """
        获取多个班级实例，并加载相关关系
        """
        query = (
            select(self.model)
            .options(
                joinedload(self.model.head_teacher),
                joinedload(self.model.users),
                joinedload(self.model.students)
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.unique().scalars().all()

    async def get_by_name_and_year(
        self, db: AsyncSession, *, name: str, year: int
    ) -> Optional[Classes]:
        """
        通过班级名称和年份获取班级
        """
        query = select(self.model).where(
            self.model.name == name,
            self.model.year == year
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_head_teacher(
        self, db: AsyncSession, *, head_teacher_id: int
    ) -> List[Classes]:
        """获取教师负责的班级"""
        query = select(Classes).where(Classes.head_teacher_id == head_teacher_id)
        result = await db.execute(query)
        return result.scalars().all()

# 创建全局班级CRUD实例
class_crud = CRUDClass(Classes)
