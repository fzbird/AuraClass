from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.class_crud import class_crud
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.class_schema import Classes, ClassCreate, ClassUpdate, ClassListResponse

router = APIRouter()

@router.get("/", response_model=ClassListResponse)
async def read_classes(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = require_permissions(path="/api/v1/classes", method="GET")
) -> Any:
    """
    获取班级列表
    """
    classes = await class_crud.get_multi(db, skip=skip, limit=limit)
    total = len(classes)  # 实际项目中应该进行COUNT查询
    
    return {
        "data": classes,
        "meta": {
            "pagination": {
                "page": skip // limit + 1,
                "size": limit,
                "total": total
            }
        }
    }

@router.post("/", response_model=Classes)
async def create_class(
    *,
    db: AsyncSession = Depends(get_db),
    class_in: ClassCreate,
    current_user: User = require_permissions(path="/api/v1/classes", method="POST")
) -> Any:
    """
    创建新班级
    """
    # 检查同名同年级班级是否已存在
    existing_class = await class_crud.get_by_name_and_year(
        db, name=class_in.name, year=class_in.year
    )
    if existing_class:
        raise HTTPException(
            status_code=400,
            detail=f"{class_in.year}年级已存在名为{class_in.name}的班级"
        )
    
    # 处理 head_teacher_id
    if hasattr(class_in, 'head_teacher_id'):
        if class_in.head_teacher_id == 0:
            class_in.head_teacher_id = None
        elif class_in.head_teacher_id is not None:
            # 检查教师是否存在
            teacher = await CRUDUser.get(db, id=class_in.head_teacher_id)
            if not teacher:
                raise HTTPException(
                    status_code=400,
                    detail=f"ID为 {class_in.head_teacher_id} 的教师不存在"
                )
    
    class_obj = await class_crud.create(db, obj_in=class_in)
    return class_obj

@router.get("/{class_id}", response_model=Classes)
async def read_class(
    *,
    db: AsyncSession = Depends(get_db),
    class_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/classes/{class_id}", method="GET")
) -> Any:
    """
    获取指定班级
    """
    class_obj = await class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=404,
            detail="班级不存在"
        )
    return class_obj

@router.put("/{class_id}", response_model=Classes)
async def update_class(
    *,
    db: AsyncSession = Depends(get_db),
    class_id: int = Path(..., gt=0),
    class_in: ClassUpdate,
    current_user: User = require_permissions(path="/api/v1/classes/{class_id}", method="PUT")
) -> Any:
    """
    更新班级
    """
    class_obj = await class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=404,
            detail="班级不存在"
        )
    
    # 检查更新后的班级名称是否与其他班级冲突
    if class_in.name and class_in.name != class_obj.name and class_in.year:
        existing_class = await class_crud.get_by_name_and_year(
            db, name=class_in.name, year=class_in.year
        )
        if existing_class and existing_class.id != class_id:
            raise HTTPException(
                status_code=400,
                detail=f"{class_in.year}年级已存在名为{class_in.name}的班级"
            )
    
    class_obj = await class_crud.update(db, db_obj=class_obj, obj_in=class_in)
    return class_obj

@router.delete("/{class_id}", response_model=None, status_code=204)
async def delete_class(
    *,
    db: AsyncSession = Depends(get_db),
    class_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/classes/{class_id}", method="DELETE")
) -> None:
    """
    删除班级
    """
    class_obj = await class_crud.get(db, id=class_id)
    if not class_obj:
        raise HTTPException(
            status_code=404,
            detail="班级不存在"
        )
    
    # 实际开发中应检查班级是否有关联学生
    
    await class_crud.remove(db, id=class_id)
    return None
