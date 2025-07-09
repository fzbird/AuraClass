from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.quant_item_category import quant_item_category as category_crud
from app.models.user import User
from app.schemas.quant_item_category import (
    QuantItemCategory,
    QuantItemCategoryCreate,
    QuantItemCategoryUpdate,
    QuantItemCategoryListResponse
)

router = APIRouter()

@router.get("/", response_model=QuantItemCategoryListResponse)
async def read_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    current_user: User = require_permissions(path="/api/v1/quant-item-categories", method="GET")
) -> Any:
    """
    获取量化项目分类列表
    """
    if active_only:
        categories = await category_crud.get_all_active(db, skip=skip, limit=limit)
    else:
        categories = await category_crud.get_all_ordered(db, skip=skip, limit=limit)
    
    total = len(categories)  # 实际项目中应该进行COUNT查询
    
    return {
        "data": categories,
        "meta": {
            "pagination": {
                "page": skip // limit + 1,
                "size": limit,
                "total": total
            }
        }
    }

@router.post("/", response_model=QuantItemCategory)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: QuantItemCategoryCreate,
    current_user: User = require_permissions(path="/api/v1/quant-item-categories", method="POST")
) -> Any:
    """
    创建新的量化项目分类
    """
    # 检查名称是否已存在
    existing_category = await category_crud.get_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"名称为{category_in.name}的分类已存在"
        )
    
    category = await category_crud.create(db, obj_in=category_in)
    return category

@router.get("/{category_id}", response_model=QuantItemCategory)
async def read_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-item-categories/{category_id}", method="GET")
) -> Any:
    """
    获取指定的量化项目分类
    """
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="分类不存在"
        )
    return category

@router.put("/{category_id}", response_model=QuantItemCategory)
async def update_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: int = Path(..., gt=0),
    category_in: QuantItemCategoryUpdate,
    current_user: User = require_permissions(path="/api/v1/quant-item-categories/{category_id}", method="PUT")
) -> Any:
    """
    更新量化项目分类
    """
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="分类不存在"
        )
    
    # 检查更新后的名称是否与其他分类冲突
    if category_in.name and category_in.name != category.name:
        existing_category = await category_crud.get_by_name(db, name=category_in.name)
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=400,
                detail=f"名称为{category_in.name}的分类已存在"
            )
    
    category = await category_crud.update(db, db_obj=category, obj_in=category_in)
    return category

@router.delete("/{category_id}", response_model=None, status_code=204)
async def delete_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-item-categories/{category_id}", method="DELETE")
) -> None:
    """
    删除量化项目分类
    """
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="分类不存在"
        )
    
    # 实际开发中应检查分类是否有关联的量化项目
    
    await category_crud.remove(db, id=category_id)
    return None

@router.patch("/{category_id}/active", response_model=QuantItemCategory)
async def toggle_category_active(
    *,
    db: AsyncSession = Depends(get_db),
    category_id: int = Path(..., gt=0),
    active: bool,
    current_user: User = require_permissions(path="/api/v1/quant-item-categories/{category_id}/active", method="PATCH")
) -> Any:
    """
    启用/禁用量化项目分类
    """
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="分类不存在"
        )
    
    category = await category_crud.update(db, db_obj=category, obj_in={"is_active": active})
    return category 