import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from passlib.context import CryptContext

from app.db.session import AsyncSessionLocal, get_db
from app.core.security import get_password_hash
from app.core.logging import get_logger
from app.models.role import Role
from app.models.user import User
from app.crud.role import create_role
from app.crud.user import create_user
from app.schemas.role import RoleCreate
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = get_logger(__name__)

async def init_db(db: AsyncSession) -> None:
    """
    初始化数据库，创建默认角色和管理员用户
    """
    try:
        # 创建默认角色
        roles = [
            {"name": "admin", "description": "系统管理员，拥有所有权限"},
            {"name": "teacher", "description": "教师用户，可管理学生和量化记录"},
            {"name": "student", "description": "学生用户，只能查看自己的信息"}
        ]
        
        role_ids = {}
        for role_data in roles:
            role = await create_role(db, RoleCreate(**role_data))
            role_ids[role.name] = role.id
            logger.info(f"角色已创建: {role.name}")
        
        # 创建管理员用户
        admin_data = {
            "username": "admin",
            "password": "admin@123",
            "full_name": "系统管理员",
            "role_id": role_ids["admin"],
            "is_active": True
        }
        
        admin_user = await create_user(db, UserCreate(**admin_data))
        logger.info(f"管理员用户已创建: {admin_user.username}")
        
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

# 运行初始化脚本
if __name__ == "__main__":
    asyncio.run(init_db(AsyncSessionLocal()))
