from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.quant_item_category import QuantItemCategory
from app.schemas.quant_item_category import QuantItemCategoryCreate, QuantItemCategoryUpdate

class CRUDQuantItemCategory(CRUDBase[QuantItemCategory, QuantItemCategoryCreate, QuantItemCategoryUpdate]):
    async def get_by_name(
        self, db: AsyncSession, *, name: str
    ) -> Optional[QuantItemCategory]:
        """通过名称获取量化项目分类"""
        query = select(QuantItemCategory).where(QuantItemCategory.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[QuantItemCategory]:
        """获取所有激活的项目分类"""
        query = select(QuantItemCategory).where(
            QuantItemCategory.is_active == True
        ).order_by(
            QuantItemCategory.order.asc()
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_all_ordered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[QuantItemCategory]:
        """获取所有项目分类，按排序字段排序"""
        query = select(QuantItemCategory).order_by(
            QuantItemCategory.order.asc()
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

# 创建全局量化项目分类CRUD实例
quant_item_category = CRUDQuantItemCategory(QuantItemCategory) 