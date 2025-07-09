from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.quant_item import QuantItem
from app.schemas.quant_item import QuantItemCreate, QuantItemUpdate

class CRUDQuantItem(CRUDBase[QuantItem, QuantItemCreate, QuantItemUpdate]):
    async def get_by_name(
        self, db: AsyncSession, *, name: str
    ) -> Optional[QuantItem]:
        """通过名称获取量化项目"""
        query = select(QuantItem).where(QuantItem.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_category(
        self, db: AsyncSession, *, category: str
    ) -> List[QuantItem]:
        """获取特定类别的所有量化项目"""
        query = select(QuantItem).where(QuantItem.category == category)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_category_id(
        self, db: AsyncSession, *, category_id: int
    ) -> List[QuantItem]:
        """获取特定分类ID的所有量化项目"""
        query = select(QuantItem).where(QuantItem.category_id == category_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[QuantItem]:
        """获取所有激活的量化项目"""
        query = select(QuantItem).where(QuantItem.is_active == True).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

# 创建全局量化项目CRUD实例
quant_item = CRUDQuantItem(QuantItem)
