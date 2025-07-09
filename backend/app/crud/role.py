from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Role]:
        """通过名称获取角色"""
        query = select(Role).where(Role.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, db: AsyncSession) -> List[Role]:
        """获取所有角色"""
        query = select(Role)
        result = await db.execute(query)
        return result.scalars().all()

# 创建全局角色CRUD实例
role = CRUDRole(Role)
