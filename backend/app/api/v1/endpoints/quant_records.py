from datetime import date
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.permissions import require_permissions
from app.crud.quant_record import quant_record_crud
from app.models.user import User
from app.schemas.quant_record import (
    QuantRecord, QuantRecordCreate, QuantRecordUpdate, 
    QuantRecordListResponse, QuantRecordBatchCreate
)
from app.services.export import export_stats

router = APIRouter()

@router.get("/", response_model=List[QuantRecord])
async def read_quant_records(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None, gt=0),
    item_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = require_permissions(path="/api/v1/quant-records", method="GET")
) -> Any:
    """
    获取量化记录列表
    """
    # 根据提供的参数决定查询方法
    if start_date and end_date:
        # 日期范围查询
        result = await quant_record_crud.get_by_date_range(
            db, start_date=start_date, end_date=end_date,
            student_id=student_id, item_id=item_id,
            skip=skip, limit=limit
        )
    elif student_id and item_id:
        # 同时按学生和项目查询
        result = await quant_record_crud.get_by_student_and_item(
            db, student_id=student_id, item_id=item_id,
            skip=skip, limit=limit
        )
    elif student_id:
        # 按学生查询
        result = await quant_record_crud.get_by_student(
            db, student_id=student_id, skip=skip, limit=limit
        )
    elif item_id:
        # 按项目查询
        result = await quant_record_crud.get_by_item(
            db, item_id=item_id, skip=skip, limit=limit
        )
    else:
        # 普通分页查询
        result = await quant_record_crud.get_multi_with_details(db, skip=skip, limit=limit)

    # 处理关联查询结果，统一返回格式
    records = []
    for record_data in result:
        # 检查元组长度以适应不同的返回格式
        if len(record_data) == 5:  # 新格式：(QuantRecord, Student, QuantItem, User, Classes)
            record, student, item, recorder, class_obj = record_data
        else:  # 旧格式：(QuantRecord, Student, QuantItem, User)
            record, student, item, recorder = record_data
            class_obj = None
        
        record_dict = record.__dict__
        record_dict["student_name"] = student.full_name
        record_dict["item_name"] = item.name
        record_dict["recorder_name"] = recorder.full_name if recorder else ""
        # 添加班级名称（如果可用）
        if class_obj:
            record_dict["class_name"] = class_obj.name
        
        records.append(record_dict)
    
    # 直接返回记录数组
    return records

@router.post("/", response_model=QuantRecord)
async def create_quant_record(
    *,
    db: AsyncSession = Depends(get_db),
    record_in: QuantRecordCreate,
    current_user: User = require_permissions(path="/api/v1/quant-records", method="POST")
) -> Any:
    """
    创建新量化记录
    """
    # 设置记录者为当前用户
    record_in.recorder_id = current_user.id
    
    record = await quant_record_crud.create(db, obj_in=record_in)
    
    # 获取记录的详细信息
    result = await quant_record_crud.get_record_with_details(db, record_id=record.id)
    if not result:
        # 这种情况应该不会发生，因为我们刚刚创建了记录
        return record
    
    # 构造响应
    record, student, item, recorder = result
    record_dict = record.__dict__
    record_dict["student_name"] = student.full_name
    record_dict["item_name"] = item.name
    record_dict["recorder_name"] = recorder.full_name
    
    return record_dict

@router.post("/batch", status_code=201)
async def create_quant_records_batch(
    *,
    db: AsyncSession = Depends(get_db),
    batch_in: QuantRecordBatchCreate,
    current_user: User = require_permissions(path="/api/v1/quant-records/batch", method="POST")
) -> Any:
    """
    批量创建量化记录
    """
    # 设置记录者为当前用户
    for record_in in batch_in.records:
        record_in.recorder_id = current_user.id
    
    created_count = await quant_record_crud.create_batch(db, obj_in_list=batch_in.records)
    
    return {
        "message": f"成功创建{created_count}条记录",
        "data": {
            "created": created_count
        }
    }

@router.get("/export", response_class=FileResponse)
async def export_quant_records(
    db: AsyncSession = Depends(get_db),
    student_id: Optional[int] = Query(None, gt=0),
    class_id: Optional[int] = Query(None, gt=0),
    item_id: Optional[int] = Query(None, gt=0),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", regex="^(csv|excel)$"),
    limit: int = Query(1000, gt=0, le=5000),
    current_user: User = require_permissions(path="/api/v1/quant-records/export", method="GET")
) -> Any:
    """
    导出量化记录数据
    支持按学生、班级、项目、类别、日期范围等条件筛选
    支持导出为CSV或Excel格式
    """
    filters = {
        "student_id": student_id,
        "class_id": class_id,
        "item_id": item_id, 
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }
    
    # 使用通用导出服务
    return await export_stats(
        db=db, 
        type="records", 
        format=format, 
        filters=filters
    )

@router.get("/{record_id}", response_model=QuantRecord)
async def read_quant_record(
    *,
    db: AsyncSession = Depends(get_db),
    record_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-records/{record_id}", method="GET")
) -> Any:
    """
    获取指定量化记录
    """
    result = await quant_record_crud.get_record_with_details(db, record_id=record_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="量化记录不存在"
        )
    
    # 构造响应，处理可能的5元素元组
    if len(result) == 5:
        record, student, item, recorder, class_obj = result
    else:
        record, student, item, recorder = result
        class_obj = None
    
    record_dict = record.__dict__
    record_dict["student_name"] = student.full_name
    record_dict["item_name"] = item.name
    record_dict["recorder_name"] = recorder.full_name if recorder else ""
    
    # 添加班级名称（如果可用）
    if class_obj:
        record_dict["class_name"] = class_obj.name
    
    return record_dict

@router.put("/{record_id}", response_model=QuantRecord)
async def update_quant_record(
    *,
    db: AsyncSession = Depends(get_db),
    record_id: int = Path(..., gt=0),
    record_in: QuantRecordUpdate,
    current_user: User = require_permissions(path="/api/v1/quant-records/{record_id}", method="PUT")
) -> Any:
    """
    更新量化记录
    """
    record = await quant_record_crud.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="量化记录不存在"
        )
    
    record = await quant_record_crud.update(db, db_obj=record, obj_in=record_in)
    
    # 获取更新后的详细信息
    result = await quant_record_crud.get_record_with_details(db, record_id=record.id)
    if not result:
        return record
    
    # 构造响应，处理可能的5元素元组
    if len(result) == 5:
        record, student, item, recorder, class_obj = result
    else:
        record, student, item, recorder = result
        class_obj = None
    
    record_dict = record.__dict__
    record_dict["student_name"] = student.full_name
    record_dict["item_name"] = item.name
    record_dict["recorder_name"] = recorder.full_name if recorder else ""
    
    # 添加班级名称（如果可用）
    if class_obj:
        record_dict["class_name"] = class_obj.name
    
    return record_dict

@router.delete("/{record_id}", response_model=None, status_code=204)
async def delete_quant_record(
    *,
    db: AsyncSession = Depends(get_db),
    record_id: int = Path(..., gt=0),
    current_user: User = require_permissions(path="/api/v1/quant-records/{record_id}", method="DELETE")
) -> None:
    """
    删除量化记录
    """
    record = await quant_record_crud.get(db, id=record_id)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="量化记录不存在"
        )
    
    await quant_record_crud.remove(db, id=record_id)
    return None
