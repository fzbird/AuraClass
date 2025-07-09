from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.student import student as student_crud
from app.models.user import User
from app.schemas.student import Student, StudentCreate, StudentUpdate, StudentListResponse
from app.models.quant_record import QuantRecord

router = APIRouter()

@router.get("/", response_model=StudentListResponse)
async def read_students(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数量"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    name: Optional[str] = Query(None, description="学生姓名，支持模糊搜索"),
    student_id_no: Optional[str] = Query(None, description="学号，支持模糊搜索"),
    gender: Optional[str] = Query(None, description="性别，male或female"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    sort_by: str = Query("id", description="排序字段: id, total_score, rank"),
    sort_order: str = Query("asc", description="排序方向: asc, desc"),
    current_user: User = require_permissions(path="/api/v1/students", method="GET")
) -> Any:
    """
    获取学生列表，支持多条件组合查询
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的记录数量
    - **class_id**: 按班级ID筛选
    - **name**: 按学生姓名筛选（支持模糊搜索）
    - **student_id_no**: 按学号筛选（支持模糊搜索）
    - **gender**: 按性别筛选 (male/female)
    - **is_active**: 按状态筛选（true/false）
    - **sort_by**: 排序字段
    - **sort_order**: 排序方向
    """
    # 构建查询条件
    filters = {}
    if class_id is not None:
        filters["class_id"] = class_id
    if name is not None:
        filters["name"] = name
    if student_id_no is not None:
        filters["student_id_no"] = student_id_no
    if gender is not None:
        filters["gender"] = gender
    if is_active is not None:
        filters["is_active"] = is_active
    
    # 根据条件获取学生列表
    students, total = await student_crud.get_students_with_filters(
        db, 
        filters=filters,
        skip=skip, 
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return {
        "data": students,
        "meta": {
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total
            }
        }
    }

@router.post("/", response_model=Student)
async def create_student(
    *,
    db: AsyncSession = Depends(get_db),
    student_in: StudentCreate,
    current_user: User = require_permissions(path="/api/v1/students", method="POST")
) -> Any:
    """
    创建新学生
    """
    # 检查学号是否已存在
    existing_student = await student_crud.get_by_student_id_no(
        db, student_id_no=student_in.student_id_no
    )
    if existing_student:
        raise HTTPException(
            status_code=400,
            detail=f"学号为{student_in.student_id_no}的学生已存在"
        )
    
    student_obj = await student_crud.create(db, obj_in=student_in)
    return student_obj

@router.get("/{student_id}", response_model=Student)
async def read_student(
    *,
    db: AsyncSession = Depends(get_db),
    student_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/students/{student_id}", method="GET")
) -> Any:
    """
    获取指定学生
    """
    student_obj = await student_crud.get(db, id=student_id)
    if not student_obj:
        raise HTTPException(
            status_code=404,
            detail="学生不存在"
        )
    return student_obj

@router.put("/{student_id}", response_model=Student)
async def update_student(
    *,
    db: AsyncSession = Depends(get_db),
    student_id: int = Path(..., gt=0),
    student_in: StudentUpdate,
    current_user: User = require_permissions(path="/api/v1/students/{student_id}", method="PUT")
) -> Any:
    """
    更新学生
    """
    student_obj = await student_crud.get(db, id=student_id)
    if not student_obj:
        raise HTTPException(
            status_code=404,
            detail="学生不存在"
        )
    
    # 检查更新后的学号是否与其他学生冲突
    if student_in.student_id_no and student_in.student_id_no != student_obj.student_id_no:
        existing_student = await student_crud.get_by_student_id_no(
            db, student_id_no=student_in.student_id_no
        )
        if existing_student and existing_student.id != student_id:
            raise HTTPException(
                status_code=400,
                detail=f"学号为{student_in.student_id_no}的学生已存在"
            )
    
    student_obj = await student_crud.update(db, db_obj=student_obj, obj_in=student_in)
    return student_obj

@router.delete("/{student_id}", response_model=None, status_code=204)
async def delete_student(
    *,
    db: AsyncSession = Depends(get_db),
    student_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/students/{student_id}", method="DELETE")
) -> None:
    """
    删除学生
    """
    student_obj = await student_crud.get(db, id=student_id)
    if not student_obj:
        raise HTTPException(
            status_code=404,
            detail="学生不存在"
        )
    
    # 检查学生是否有关联的量化记录
    query = select(func.count(QuantRecord.id)).where(QuantRecord.student_id == student_id)
    result = await db.execute(query)
    record_count = result.scalar_one()
    
    if record_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该学生有{record_count}条量化记录，无法删除",
            headers={"X-Record-Count": str(record_count)}
        )
    
    await student_crud.remove(db, id=student_id)
    return None

@router.delete("/{student_id}/force", response_model=dict)
async def force_delete_student(
    *,
    db: AsyncSession = Depends(get_db),
    student_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/students/{student_id}/force", method="DELETE")
) -> Any:
    """
    强制删除学生及其所有关联的量化记录
    """
    student_obj = await student_crud.get(db, id=student_id)
    if not student_obj:
        raise HTTPException(
            status_code=404,
            detail="学生不存在"
        )
    
    # 删除学生关联的量化记录
    delete_records_query = delete(QuantRecord).where(QuantRecord.student_id == student_id)
    result = await db.execute(delete_records_query)
    deleted_records_count = result.rowcount
    
    # 删除学生
    await student_crud.remove(db, id=student_id)
    
    return {
        "success": True,
        "message": f"已删除学生及{deleted_records_count}条关联记录",
        "deleted_records_count": deleted_records_count
    }

@router.patch("/{student_id}/active", response_model=Student)
async def toggle_student_active(
    *,
    db: AsyncSession = Depends(get_db),
    student_id: int = Path(..., gt=0),
    active: bool,
    current_user: User = require_permissions(path="/api/v1/students/{student_id}/active", method="PATCH")
) -> Any:
    """
    启用/禁用学生
    """
    student_obj = await student_crud.get(db, id=student_id)
    if not student_obj:
        raise HTTPException(
            status_code=404,
            detail="学生不存在"
        )
    
    student_obj = await student_crud.update(db, db_obj=student_obj, obj_in={"is_active": active})
    return student_obj

@router.post("/update-scores", response_model=dict)
async def update_student_scores(
    *,
    db: AsyncSession = Depends(get_db),
    class_id: Optional[int] = Query(None, gt=0),
    current_user: User = require_permissions(path="/api/v1/students/update-scores", method="POST")
) -> Any:
    """
    更新学生总分和排名
    """
    updated_count = await student_crud.update_scores_and_ranks(db, class_id=class_id)
    return {
        "success": True,
        "message": f"已更新 {updated_count} 名学生的分数和排名",
        "updated_count": updated_count
    }
