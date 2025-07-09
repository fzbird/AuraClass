from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.user import user as user_crud
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, UserListResponse

router = APIRouter()

@router.get("/", response_model=UserListResponse)
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = require_permissions(path="/api/v1/users", method="GET")
) -> Any:
    """
    获取用户列表
    """
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    total = len(users)  # 实际项目中应该进行COUNT查询
    
    return {
        "data": users,
        "meta": {
            "pagination": {
                "page": skip // limit + 1,
                "size": limit,
                "total": total
            }
        }
    }

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = require_permissions(path="/api/v1/users", method="POST")
) -> Any:
    """
    创建新用户
    """
    user = await user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    
    user = await user_crud.create(db, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/users/{user_id}", method="GET")
) -> Any:
    """
    获取指定用户
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int = Path(..., gt=0),
    user_in: UserUpdate,
    current_user: User = require_permissions(path="/api/v1/users/{user_id}", method="PUT")
) -> Any:
    """
    更新用户
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    # 验证 class_id
    if hasattr(user_in, 'class_id') and user_in.class_id is not None and user_in.class_id == 0:
        user_in.class_id = None  # 将 0 转换为 None
    
    # 验证 role_id
    if hasattr(user_in, 'role_id') and user_in.role_id == 0:
        raise HTTPException(
            status_code=400,
            detail="无效的角色ID"
        )
    
    user = await user_crud.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=None, status_code=204)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/users/{user_id}", method="DELETE")
) -> None:
    """
    删除用户
    """
    user = await user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    await user_crud.remove(db, id=user_id)
    return None
