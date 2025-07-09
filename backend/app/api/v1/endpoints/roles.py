from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.role import role as role_crud
from app.models.user import User
from app.schemas.role import Role, RoleCreate, RoleUpdate, RoleListResponse

router = APIRouter()

@router.get("/", response_model=RoleListResponse)
async def read_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = require_permissions(path="/api/v1/roles", method="GET")
) -> Any:
    """
    获取所有角色
    """
    roles = await role_crud.get_all(db)
    
    return {
        "data": roles,
        "meta": {
            "total": len(roles)
        }
    }

@router.post("/", response_model=Role)
async def create_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_in: RoleCreate,
    current_user: User = require_permissions(path="/api/v1/roles", method="POST")
) -> Any:
    """
    创建新角色
    """
    role = await role_crud.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=400,
            detail="角色名已存在"
        )
    
    role = await role_crud.create(db, obj_in=role_in)
    return role

@router.get("/{role_id}", response_model=Role)
async def read_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/roles/{role_id}", method="GET")
) -> Any:
    """
    获取指定角色
    """
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    return role

@router.put("/{role_id}", response_model=Role)
async def update_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: int = Path(..., gt=0),
    role_in: RoleUpdate,
    current_user: User = require_permissions(path="/api/v1/roles/{role_id}", method="PUT")
) -> Any:
    """
    更新角色
    """
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    
    # 检查更新的角色名是否已存在
    if role_in.name and role_in.name != role.name:
        existing_role = await role_crud.get_by_name(db, name=role_in.name)
        if existing_role:
            raise HTTPException(
                status_code=400,
                detail="角色名已存在"
            )
    
    role = await role_crud.update(db, db_obj=role, obj_in=role_in)
    return role

@router.delete("/{role_id}", response_model=None, status_code=204)
async def delete_role(
    *,
    db: AsyncSession = Depends(get_db),
    role_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/roles/{role_id}", method="DELETE")
) -> None:
    """
    删除角色
    """
    role = await role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=404,
            detail="角色不存在"
        )
    
    # 检查角色是否有关联用户
    # 实际开发中应该添加这个检查
    
    await role_crud.remove(db, id=role_id)
    return None
