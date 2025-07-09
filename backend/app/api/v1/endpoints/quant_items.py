from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.quant_item import quant_item as quant_item_crud
from app.crud.quant_item_category import quant_item_category as category_crud
from app.models.user import User
from app.schemas.quant_item import QuantItem, QuantItemCreate, QuantItemUpdate, QuantItemListResponse

router = APIRouter()

@router.get("/", response_model=QuantItemListResponse)
async def read_quant_items(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None, gt=0),
    active_only: bool = Query(False),
    current_user: User = require_permissions(path="/api/v1/quant-items", method="GET")
) -> Any:
    """
    获取量化项目列表
    """
    if category_id:
        items = await quant_item_crud.get_by_category_id(db, category_id=category_id)
        if active_only:
            items = [item for item in items if item.is_active]
    elif category:
        items = await quant_item_crud.get_by_category(db, category=category)
        if active_only:
            items = [item for item in items if item.is_active]
    elif active_only:
        items = await quant_item_crud.get_active(db, skip=skip, limit=limit)
    else:
        items = await quant_item_crud.get_multi(db, skip=skip, limit=limit)
    
    total = len(items)  # 实际项目中应该进行COUNT查询
    
    return {
        "data": items,
        "meta": {
            "pagination": {
                "page": skip // limit + 1 if not (category or category_id) else 1,
                "size": limit if not (category or category_id) else total,
                "total": total
            }
        }
    }

@router.post("/", response_model=QuantItem)
async def create_quant_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: QuantItemCreate,
    current_user: User = require_permissions(path="/api/v1/quant-items", method="POST")
) -> Any:
    """
    创建新量化项目
    """
    # 检查名称是否已存在
    existing_item = await quant_item_crud.get_by_name(db, name=item_in.name)
    if existing_item:
        raise HTTPException(
            status_code=400,
            detail=f"名称为{item_in.name}的量化项目已存在"
        )
    
    # 如果提供了分类ID，检查分类是否存在
    if item_in.category_id:
        category = await category_crud.get(db, id=item_in.category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"分类ID为{item_in.category_id}的分类不存在"
            )
        # 如果分类存在，自动设置category字段为分类名称，保持一致性
        item_in.category = category.name
    
    item = await quant_item_crud.create(db, obj_in=item_in)
    return item

@router.get("/{item_id}", response_model=QuantItem)
async def read_quant_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-items/{item_id}", method="GET")
) -> Any:
    """
    获取指定量化项目
    """
    item = await quant_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="量化项目不存在"
        )
    return item

@router.put("/{item_id}", response_model=QuantItem)
async def update_quant_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int = Path(..., gt=0),
    item_in: QuantItemUpdate,
    current_user: User = require_permissions(path="/api/v1/quant-items/{item_id}", method="PUT")
) -> Any:
    """
    更新量化项目
    """
    item = await quant_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="量化项目不存在"
        )
    
    # 检查更新后的名称是否与其他项目冲突
    if item_in.name and item_in.name != item.name:
        existing_item = await quant_item_crud.get_by_name(db, name=item_in.name)
        if existing_item and existing_item.id != item_id:
            raise HTTPException(
                status_code=400,
                detail=f"名称为{item_in.name}的量化项目已存在"
            )
    
    # 如果提供了分类ID，检查分类是否存在并更新category字段
    if item_in.category_id:
        category = await category_crud.get(db, id=item_in.category_id)
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"分类ID为{item_in.category_id}的分类不存在"
            )
        # 如果分类存在，自动设置category字段为分类名称，保持一致性
        item_in.category = category.name
    
    item = await quant_item_crud.update(db, db_obj=item, obj_in=item_in)
    return item

@router.delete("/{item_id}", response_model=None, status_code=204)
async def delete_quant_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-items/{item_id}", method="DELETE")
) -> None:
    """
    删除量化项目
    """
    item = await quant_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="量化项目不存在"
        )
    
    # 实际开发中应检查项目是否有关联记录
    
    await quant_item_crud.remove(db, id=item_id)
    return None

@router.patch("/{item_id}/active", response_model=QuantItem)
async def toggle_quant_item_active(
    *,
    db: AsyncSession = Depends(get_db),
    item_id: int = Path(..., gt=0),
    active: bool,
    current_user: User = require_permissions(path="/api/v1/quant-items/{item_id}/active", method="PATCH")
) -> Any:
    """
    启用/禁用量化项目
    """
    item = await quant_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="量化项目不存在"
        )
    
    item = await quant_item_crud.update(db, db_obj=item, obj_in={"is_active": active})
    return item
